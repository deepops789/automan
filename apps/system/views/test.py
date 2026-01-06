from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser  # 新增的导入
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from system.models import faker_data
from system.serializers.testserializers import FakerDataSerializer
from system.pagination import CustomPagination
from user.models import Menu, Permission
from system.serializers.menuSerializer import MenuSerializer, PermissionSerializer

class FakerDataViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]  # 现在可以正常使用 AllowAny
    queryset = faker_data.objects.all()
    serializer_class = FakerDataSerializer
    pagination_class = CustomPagination


class GetMenu(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # 示例菜单数据
        menu_data = {
            "code": 0,
            "data": {
                "items": [
                    {
                        "id": "98436227-f888-47e1-af83-3559e2877128",
                        "imageUrl": "https://avatars.githubusercontent.com/u/30022453",
                        "imageUrl2": "https://avatars.githubusercontent.com/u/63203513",
                        "open": "true",
                        "status": "success",
                        "productName": "Fresh Steel Mouse",
                        "price": "820.05",
                        "currency": "BTN",
                        "quantity": 1,
                        "available": "false",
                        "category": "Toys",
                        "releaseDate": "2024-04-06T09:03:50.927Z",
                        "rating": 3.318978457116943,
                        "description": "Discover the upset new Car with an exciting mix of Plastic ingredients",
                        "weight": 5.1224226380747995,
                        "color": "teal",
                        "inProduction": "false",
                        "tags": ["Handcrafted", "Practical", "Incredible"],
                    },
                    {
                        "id": "50f801dc-d457-4443-a87c-f2fd28849853",
                        "imageUrl": "https://avatars.githubusercontent.com/u/31204739",
                        "imageUrl2": "https://avatars.githubusercontent.com/u/71339845",
                        "open": "true",
                        "status": "warning",
                        "productName": "Handcrafted Silk Cheese",
                        "price": "536.45",
                        "currency": "KHR",
                        "quantity": 37,
                        "available": "true",
                        "category": "Music",
                        "releaseDate": "2025-02-08T15:58:20.815Z",
                        "rating": 3.444983455996876,
                        "description": "Frozen Bike designed with Silk for bad performance",
                        "weight": 3.482607794537867,
                        "color": "silver",
                        "inProduction": "false",
                        "tags": ["Practical", "Oriental", "Frozen"],
                    },
                ],
                "total": 100,
            },
            "error": "",
            "message": "ok",
        }
        return Response(menu_data, status=status.HTTP_200_OK)


class MenuApiView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        queryset = Menu.objects.all()
        pagination_class = CustomPagination
        serializer = MenuSerializer(queryset, many=True)
        return Response(
            {
                "code": 0,
                "data": {
                    "items": serializer.data,
                    #         "items": [
                    #     {
                    #         "id": 1,
                    #         "title": "系统设置",
                    #         "icon": "system-uicons:settings",
                    #         "path": "null",
                    #         "is_frame": "false",
                    #         "is_show": "true",
                    #         "sort": "null",
                    #         "permissions": [
                    #             {
                    #                 "id": 1,
                    #                 "title": "权限设置",
                    #                 "icon": "icon-park:menu-fold-one",
                    #                 "path": "/test",
                    #                 "component": "/dashboard/test/index",
                    #                 "method": "null",
                    #                 "permissions": [{ "title": "按钮1" },{ "path": "32" }],
                    #                 "button_codes": []
                    #             },
                    #             {
                    #                 "id": 2,
                    #                 "title": "菜单设置",
                    #                  "icon": "uis:lock-access",
                    #                 "path": "/test2",
                    #                 "component": "/dashboard/system/menu/index",
                    #                 "method": "null",
                    #                 "button_codes": []
                    #             }
                    #         ]
                    #     }
                    # ],
                    "total": queryset.count(),
                },
                "error": "",
                "message": "ok",
            }
        )

    def post(self, request):
        serializer = MenuSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 0, "message": "created"})
        return Response({"code": 1, "error": serializer.errors})


class CreateMenuOrPerm(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        print(request.data)
        return Response({"code": 1, "error": "11"})
    def put(self, request):
        print(request.data)
        print("请求方法:", request.method)
        return Response({"code": 1, "error": "11"})

    def post(self, request):
        data = request.data.get('data', {})
        print(data)
        types = data.pop('types', None)
        serializer = None
        if types == 'menu':
            serializer = MenuSerializer(data=data)
            print(data)
        elif types == 'permission':
            serializer = PermissionSerializer(data=data)   
        elif types == 'button':
            # button_codes 是 Permission 表的主 id
            permission_id = data.pop('button_id', None)
            # 获取对应的 Permission 对象
            permission = Permission.objects.get(id=permission_id)
            
            # 准备要写入 button_codes 的数据（排除 button_codes 主 id、is_show 和 menu 字段）
            button_data = {}
            for k, v in data.items():
                if k == 'button_codes' or k == 'is_show' or k == 'menu':
                    continue
                # 将 permissionCode 改名为 component
                if k == 'permissionCode':
                    button_data['component'] = v
                else:
                    button_data[k] = v
            
            # 直接访问模型字段获取现有的 button_codes 列表（效率更高）
            current_button_codes = permission.button_codes if permission.button_codes else []
            if not isinstance(current_button_codes, list):
                current_button_codes = []
            
            # 将新数据添加到 button_codes 列表中
            current_button_codes.append(button_data)
            
            # 使用 PermissionSerializer 方式更新
            serializer = PermissionSerializer(
                permission, 
                data={'button_codes': current_button_codes}, 
                partial=True
            )
        else:
            return Response({'error': '不支持的类型'}, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer and serializer.is_valid():
            serializer.save()
            return Response({"code": 0, "message": "创建成功"})
        else:
            return Response({"code":0,"data":"null","error":"演示环境，禁止修改","message":"演示环境，禁止修改"})

    def delete(self, request):
        print("请求数据:", request.data)
        
        # 获取 _X_ROW_SEQ 参数
        row_seq = request.data.get('_X_ROW_SEQ', '')
        print(f"_X_ROW_SEQ 值: {row_seq}")
        
        if not row_seq:
            print("错误: 缺少 _X_ROW_SEQ 参数")
            return Response({"code": 1, "error": "缺少 _X_ROW_SEQ 参数"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 统计点的数量来判断类型
        dot_count = row_seq.count('.')
        print(f"点的数量: {dot_count}")
        
        try:
            if dot_count == 0:
                # 不带点的是菜单，从请求数据中获取id字段
                menu_id = request.data.get('id')
                menu_id = int(menu_id)
                print(f"类型: 菜单")
                print(f"菜单ID: {menu_id}")
                print(f"操作: 将删除 Menu(id={menu_id})")
                menu = Menu.objects.get(id=menu_id)
                # 删除前判断是否有关联的权限
                related_permissions = menu.permissions.all()
                if related_permissions.exists():
                    permission_names = [str(p) for p in related_permissions]
                    error_msg = f"无法删除，请先删除关联的权限: {', '.join(permission_names)}"
                    print(f"错误: {error_msg}")
                    return Response({"code": 1, "error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
                menu.delete()
                return Response({"code": 0, "message": "菜单删除成功"})
            
            elif dot_count == 1:
                # 带1个点的是权限
                permission_id = request.data.get('id')
                print(f"类型: 权限")
                print(f"权限ID: {permission_id}")
                print(f"操作: 将删除 Permission(id={permission_id})")
                permission = Permission.objects.get(id=permission_id)
                permission.delete()
                return Response({"code": 0, "message": "权限删除成功（已确认）"})
            
            elif dot_count == 2:
                # 带2个点的是按钮，从请求数据中获取id字段作为权限ID
                permission_id = request.data.get('id')
                if permission_id is None:
                    print("错误: 按钮类型缺少 id 字段")
                    return Response({"code": 1, "error": "按钮类型缺少 id 字段"}, status=status.HTTP_400_BAD_REQUEST)
                permission_id = int(permission_id)
                
                # 获取要匹配的按钮字段（如 title 和 component）
                button_title = request.data.get('title')
                button_component = request.data.get('component')
                
                print(f"类型: 按钮")
                print(f"权限ID: {permission_id}")
                print(f"按钮标题: {button_title}")
                print(f"按钮组件: {button_component}")
                
                permission = Permission.objects.get(id=permission_id)
                current_button_codes = permission.button_codes if permission.button_codes else []
                if not isinstance(current_button_codes, list):
                    current_button_codes = []
                
                # 在 button_codes 列表中查找匹配的按钮并删除
                original_length = len(current_button_codes)
                # 根据 title 和 component 匹配要删除的按钮
                current_button_codes = [
                    btn for btn in current_button_codes 
                    if not (btn.get('title') == button_title and btn.get('component') == button_component)
                ]
                
                if len(current_button_codes) < original_length:
                    # 找到了匹配的按钮并已删除
                    serializer = PermissionSerializer(permission, data={'button_codes': current_button_codes}, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        print(f"操作: 已从 Permission(id={permission_id}) 的 button_codes 中删除匹配的按钮")
                        return Response({"code": 0, "message": "按钮删除成功"})
                    else:
                        print(f"序列化错误: {serializer.errors}")
                        return Response({"code": 1, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    print(f"错误: 未找到匹配的按钮，title={button_title}, component={button_component}")
                    return Response({"code": 1, "error": "未找到匹配的按钮"}, status=status.HTTP_404_NOT_FOUND)
            
            else:
                print(f"错误: 不支持的 _X_ROW_SEQ 格式，点的数量: {dot_count}")
                return Response({"code": 1, "error": "不支持的 _X_ROW_SEQ 格式"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Permission.DoesNotExist:
            print("错误: 权限不存在")
            return Response({"code": 1, "error": "权限不存在"}, status=status.HTTP_404_NOT_FOUND)
        except (ValueError, IndexError) as e:
            print(f"错误: 参数格式错误 - {str(e)}")
            return Response({"code": 1, "error": f"参数格式错误: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"错误: {str(e)}")
            return Response({"code": 1, "error": f"处理失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def patch(self, request):
        print(request.data)
        return Response({"code": 1, "error": "11"})
    